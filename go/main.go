package main

import (
	"encoding/csv"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"strings"
	"time"
)

type Place struct {
	ID                 string   `json:"id"`
	Name               string   `json:"name"`
	Address            string   `json:"address"`
	Lat                *float64 `json:"lat"`
	Lon                *float64 `json:"lon"`
	Source             string   `json:"source"`
	Type               string   `json:"type"`
	Phones             []string `json:"phones"`
	Instagram          string   `json:"instagram"`
	Whatsapp           string   `json:"whatsapp"`
	Website            string   `json:"website"`
	Description        string   `json:"description"`
	Infra              []string `json:"infrastructure"`
	Seg                string   `json:"segment"`
	SegScore           float64  `json:"segment_score"`
	GenDescription     string   `json:"generated_description"`
	PriorityScore      float64  `json:"priority_score"`
	PriorityBucket     string   `json:"priority_bucket"`
	ReviewsCount       *int     `json:"reviews_count"`
	Rating             *float64 `json:"rating"`
	InstagramFollowers *int     `json:"instagram_followers"`
}

func mustReadJSON(path string, out interface{}) {
	f, err := os.ReadFile(path)
	if err != nil {
		panic(err)
	}
	if err := json.Unmarshal(f, out); err != nil {
		panic(err)
	}
}

func writeFile(path, content string) {
	if err := os.WriteFile(path, []byte(content), 0644); err != nil {
		panic(err)
	}
}

func exportOutreachCSV(path string, items []Place) error {
	f, err := os.Create(path)
	if err != nil {
		return err
	}
	defer f.Close()
	w := csv.NewWriter(f)
	defer w.Flush()
	header := []string{"name", "phones", "instagram", "whatsapp", "segment", "priority_score", "bucket", "message_whatsapp_ru", "message_instagram_ru"}
	w.Write(header)
	for _, p := range items {
		phones := strings.Join(p.Phones, " | ")
		handle := p.Name
		if handle == "" && phones != "" {
			handle = phones
		}
		addrShort := strings.Split(p.Address, ",")[0]
		cta := "Готовы обсудить сегодня? Пришлю демо."
		msgW := fmt.Sprintf("Здравствуйте, %s! Мы заметили ваш объект рядом с %s. Хотим добавить на mytravel.kz: трафик туристов и бесплатное размещение. %s", handle, addrShort, cta)
		msgI := fmt.Sprintf("Привет, %s! Классное место у %s. Добавим в каталог mytravel.kz? %s", handle, addrShort, cta)
		w.Write([]string{
			p.Name, phones, p.Instagram, p.Whatsapp, p.Seg,
			fmt.Sprintf("%.1f", p.PriorityScore), p.PriorityBucket, msgW, msgI,
		})
	}
	return nil
}

func main() {
	base := filepath.Join("..", "data", "out")
	in := filepath.Join(base, "places_final.json")
	var items []Place
	mustReadJSON(in, &items)

	// новые/обновлённые (сравнить с прошлым снапшотом если есть)
	prevPath := filepath.Join(base, "places_prev.json")
	var prev []Place
	if _, err := os.Stat(prevPath); err == nil {
		mustReadJSON(prevPath, &prev)
	}
	prevIndex := map[string]Place{}
	for _, p := range prev {
		prevIndex[p.ID] = p
	}

	newCount := 0
	updatedCount := 0
	for _, p := range items {
		if _, ok := prevIndex[p.ID]; !ok {
			newCount++
		} else {
			if p.PriorityScore != prevIndex[p.ID].PriorityScore || p.Seg != prevIndex[p.ID].Seg {
				updatedCount++
			}
		}
	}

	// отчёт
	now := time.Now()
	report := strings.Builder{}
	report.WriteString(fmt.Sprintf("# Ежедневный отчёт (%s)\n\n", now.Format("2006-01-02")))
	report.WriteString(fmt.Sprintf("- Найдено новых объектов: **%d**\n", newCount))
	report.WriteString(fmt.Sprintf("- Обновлено данных: **%d**\n\n", updatedCount))

	// Топ-10
	sort.Slice(items, func(i, j int) bool { return items[i].PriorityScore > items[j].PriorityScore })
	top := 10
	if len(items) < top {
		top = len(items)
	}
	report.WriteString("## Топ-10 горячих лидов\n")
	for i := 0; i < top; i++ {
		p := items[i]
		addrShort := strings.Split(p.Address, ",")[0]
		report.WriteString(fmt.Sprintf("%d. **%s** — %.1f (%s, %s)\n", i+1, p.Name, p.PriorityScore, p.Seg, addrShort))
	}
	report.WriteString("\n")

	// статистика по нишам
	bySeg := map[string]int{}
	byRegion := map[string]int{}
	for _, p := range items {
		bySeg[p.Seg]++
		reg := strings.Split(p.Address, ",")[0]
		if reg == "" {
			reg = "Не указан"
		}
		byRegion[reg]++
	}
	report.WriteString("## Статистика по нишам\n")
	for k, v := range bySeg {
		report.WriteString(fmt.Sprintf("- %s: %d\n", k, v))
	}
	report.WriteString("\n## Статистика по регионам\n")
	for k, v := range byRegion {
		report.WriteString(fmt.Sprintf("- %s: %d\n", k, v))
	}

	// сохранить
	outReport := filepath.Join(base, "report_latest.md")
	writeFile(outReport, report.String())
	writeFile(prevPath, func() string { b, _ := json.MarshalIndent(items, "", "  "); return string(b) }())
	// outreach
	_ = exportOutreachCSV(filepath.Join(base, "outreach_list.csv"), items[:top])

	fmt.Println("[report] saved:", outReport)
}
